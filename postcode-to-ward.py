# -*- coding: utf-8 -*-
"""
Created on Thu May 16 22:14:02 2019

@author: Montel
"""

import sqlite3
from sqlite3 import Error
import csv
import re
import math

Z_SCORE_75 = 0.68 # approx 75th percentile for normal distribution


def getCityCode(postcode):
    return re.search("[A-Z]{1,2}[0-9]{1,2}[A-Z]{0,1}", postcode)


def log_mean(lq, uq):
    return 0.5 * math.log(lq * uq)


def log_var(mean, uq):
    return (math.log(uq) - mean) / Z_SCORE_75


class Model:
    def create_connection(self, db_path):
        try:
            with sqlite3.connect(db_path) as self.conn:
                self.cur = self.conn.cursor()
        except Error as e:
            print(e)
            
    def close_connection(self):
        self.conn.close()
            
    def create_schema(self):
        sql = ["""CREATE TABLE IF NOT EXISTS vicinity (
            	id integer PRIMARY KEY,
            	name text NOT NULL,
            	local_authority text NOT NULL,
            	county text NOT NULL
            	);""",
            
            """CREATE TABLE IF NOT EXISTS area_code (
                code text PRIMARY KEY
                );""",
            
            """CREATE TABLE IF NOT EXISTS has_area_code (
                vicinity_id integer NOT NULL,
                area_code_id text NOT NULL,
                proportion real NOT NULL,
                PRIMARY KEY (vicinity_id, area_code_id),
                FOREIGN KEY (vicinity_id) REFERENCES vicinity(id),
                FOREIGN KEY (area_code_id) REFERENCES area_code(code)
                );""",
            
            """CREATE TABLE IF NOT EXISTS rent_price (
            	id integer PRIMARY KEY,
            	area_code_id integer NOT NULL,
            	room_type text NOT NULL,
            	mean real NOT NULL,
            	variance real NOT NULL,
            	FOREIGN KEY (area_code_id) REFERENCES area_code(id)
            	);""",
            
            """CREATE TABLE IF NOT EXISTS green_space (
                vicinity_id integer PRIMARY KEY,
                green_use real NOT NULL,
                FOREIGN KEY (vicinity_id) REFERENCES vicinity(id)
                );"""
            ]
        
        for statement in sql:
            self.cur.execute(statement)
        self.conn.commit()

    def insert_vicinity(self, name, local_authority, county):
        
        sql = """INSERT INTO vicinity (name, local_authority, county)
                 VALUES(?, ?, ?)"""
                 
        self.cur.execute(sql, (name, local_authority, county))
        self.conn.commit()
        
        return self.cur.lastrowid
        
    def insert_area_code(self, code, vicinity_id, proportion):
        
        sql = """INSERT INTO has_area_code (vicinity_id, area_code_id, proportion)
                 VALUES(?, ?, ?)"""
                 
        self.cur.execute(sql, (vicinity_id, code, proportion))
        self.conn.commit()
        
        return self.cur.lastrowid
    
    def insert_rent_dist(self, code, room_type, mean, variance):
        
        sql = """INSERT INTO rent_price(area_code_id, room_type, mean, variance)
                 VALUES(?, ?, ?, ?)"""
                 
        self.cur.execute(sql, (code, room_type, mean, variance))
        self.conn.commit()
        
        return self.cur.lastrowid
    
    def insert_green_dist(self, vicinity_name, local_authority, green_percentage):
        
        sql = """SELECT id FROM vicinity
                 WHERE name = ?
                 AND local_authority = ?"""
                 
        self.cur.execute(sql, (vicinity_name, local_authority))
        id_vicinity = self.cur.fetchone()
        print(id_vicinity)
        
        sql = """INSERT INTO green_space(vicinity_id, green_use)
                 VALUES(?, ?)"""
                 
        self.cur.execute(sql, (id_vicinity[0], green_percentage))
        self.conn.commit()
        
boroughs = {
    "Camden" : {},
    "Greenwich" : {},
    "Hackney" : {},
    "Hammersmith and Fulham" : {},
    "Islington" : {},
    "Kensington and Chelsea" : {},
    "Lambeth" : {},
    "Lewisham" : {},
    "Southwark" : {},
    "Tower Hamlets" : {},
    "Wandsworth" : {},
    "Westminster" : {},
    "Barking and Dagenham" : {},
    "Barnet" : {},
    "Bexley" : {},
    "Brent" : {},
    "Bromley" : {},
    "Croydon" : {},
    "Ealing" : {},
    "Enfield" : {},
    "Haringey" : {},
    "Harrow" : {},
    "Havering" : {},
    "Hillingdon" : {},
    "Hounslow" : {},
    "Kingston upon Thames" : {},
    "Merton" : {},
    "Newham" : {},
    "Redbridge" : {},
    "Richmond upon Thames" : {},
    "Sutton" : {},
    "Waltham Forest" : {},
    "City of London" : {}
}

#7

def insert_rent_distributions(m):
    with open("postcode_rents.csv", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for row in reader:
            sample_size = row[2]
            
            if(sample_size.isnumeric() and int(sample_size) != 0):
                area_code = row[0]
                room_type = row[1]
                lq = float(row[4])
                uq = float(row[6])
                mean = log_mean(lq, uq)
                sigma = log_var(mean, uq)
                m.insert_rent_dist(area_code, room_type, mean, sigma)
                
def insert_green_spaces(m):
    with open("land-use-glud-ward.csv", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader)
        
        for row in reader:
            local_authority = row[1]
            vicinity = row[2]
            green_use = float(row[10])
            print(green_use)
            
            if local_authority != "City of London":
                m.insert_green_dist(vicinity, local_authority, green_use)
            
                
def get_vicinities(path):
    with open(path, newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for row in reader:
            area_code = getCityCode(row[0])
            ward = row[7]
            borough = row[10]
            
            if (area_code != None and borough in boroughs.keys()):
                london_code = area_code.group()
                
                if (ward not in boroughs[borough].keys()):
                    # create new entry for ward if not found
                    boroughs[borough][ward] = {}
                    
                # create new entry for postcode if not found 
                if (london_code in boroughs[borough][ward].keys()):
                    boroughs[borough][ward][london_code] += 1
                else:
                    boroughs[borough][ward][london_code] = 1
                    #print(london_code)

# move rent distribution insertions to insert_rent_distributions
def insert_vicinities(m):
    get_vicinities("pcd11_par11_wd11_lad11_ew_lu.csv")
    
    for b in boroughs.keys():
        for w in boroughs[b].keys():
            vicinity_id = m.insert_vicinity(w, b, "Greater London")
            total = 0
            for c in boroughs[b][w].keys():
                total += boroughs[b][w][c]
                
            for c in boroughs[b][w].keys():
                proportion = (boroughs[b][w][c] / total) * 100.0
                m.insert_area_code(c, vicinity_id, proportion)
            
m = Model()
m.create_connection("C:\\Users\Montel\.spyder-py3\db\db2.db")
m.create_schema()
#insert_rent_distributions(m)
insert_green_spaces(m)