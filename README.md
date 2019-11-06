# Neighbourhood-Search

An *ongoing* web app to recommend London neighbourhoods to live in based on a number of criteria, including room type, rent price, green space preferences and time willing to travel to your place of work.

![image](https://github.com/Montel98/Neighbourhood-Search/blob/master/static/vicinityMap.png)
<h2>Method: Calculating probability of property type in a ward being within a given price range:</h2>

<p>I decided to model the rent price <a href="https://www.codecogs.com/eqnedit.php?latex=X" target="_blank"><img src="https://latex.codecogs.com/gif.latex?X" title="X" /></a> 
 for any given room type using a Lognormal distribution:</p>
<a href="https://www.codecogs.com/eqnedit.php?latex=X\sim&space;Lognormal(\mu,\sigma^2\)" target="_blank"><img src="https://latex.codecogs.com/gif.latex?X\sim&space;Lognormal(\mu,\sigma^2\)" title="X\sim Lognormal(\mu,\sigma^2\)" /></a>

<br>
<p>As the rent price data is only being collected by postcode and not by ward, some assumptions have to be made. If we assume even distribution of postcodes in a ward, we can say:</p>

<a href="https://www.codecogs.com/eqnedit.php?latex=\mathbb{P}\left&space;(&space;x_{min}&space;<&space;X&space;<&space;x_{max}|ward&space;\right&space;)=\sum_{C}\mathbb{P}\left\(C_{i}|ward)\cdot\mathbb{P}\left\(&space;x_{min}&space;<&space;X&space;<&space;x_{max}&space;|&space;C_{i})" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\mathbb{P}\left&space;(&space;x_{min}&space;<&space;X&space;<&space;x_{max}|ward&space;\right&space;)=\sum_{C}\mathbb{P}\left\(C_{i}|ward)\cdot\mathbb{P}\left\(&space;x_{min}&space;<&space;X&space;<&space;x_{max}&space;|&space;C_{i})" title="\mathbb{P}\left ( x_{min} < X < x_{max}|ward \right )=\sum_{C}\mathbb{P}\left\(C_{i}|ward)\cdot\mathbb{P}\left\( x_{min} < X < x_{max} | C_{i})" /></a>

<p>Where
 <a href="https://www.codecogs.com/eqnedit.php?latex=C_i" target="_blank"><img src="https://latex.codecogs.com/gif.latex?C_i" title="C_i" /></a>
 is the probability of the given ward containing the postcode i and
<a href="https://www.codecogs.com/eqnedit.php?latex=ward" target="_blank"><img src="https://latex.codecogs.com/gif.latex?ward" title="ward" /></a>
 is the given ward.
</p>

<h2>More subtle: Probability that a property at a given price range is of the specified room type</h2>
<br>
<p>I made an assumption that the you are equally likely to find a room type (studio, 1 bed, 2 bed etc) in any given ward. While in reality this isn't the case, I could not find any data giving room type distrubitions. Using this assumption however, the probability that, <i>given</i> the property falls within the given price range,  it is the specified room type can be found using Bayes' Theorem:</p>

<a href="https://www.codecogs.com/eqnedit.php?latex=\mathbb{P}\left&space;(&space;room&space;|&space;x_{min}&space;<&space;X&space;<&space;x_{max}\right&space;)=&space;\frac{\mathbb{P}(&space;x_{min}&space;<&space;X&space;<&space;x_{max}&space;|&space;room)\cdot\mathbb{P}(room)&space;}{\sum_{room}\mathbb{P}(&space;x_{min}&space;<&space;X&space;<&space;x_{max}&space;|&space;room_i)\cdot\mathbb{P}(room_i)}" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\mathbb{P}\left&space;(&space;room&space;|&space;x_{min}&space;<&space;X&space;<&space;x_{max}\right&space;)=&space;\frac{\mathbb{P}(&space;x_{min}&space;<&space;X&space;<&space;x_{max}&space;|&space;room)\cdot\mathbb{P}(room)&space;}{\sum_{room}\mathbb{P}(&space;x_{min}&space;<&space;X&space;<&space;x_{max}&space;|&space;room_i)\cdot\mathbb{P}(room_i)}" title="\mathbb{P}\left ( room | x_{min} < X < x_{max}\right )= \frac{\mathbb{P}( x_{min} < X < x_{max} | room)\cdot\mathbb{P}(room) }{\sum_{room}\mathbb{P}( x_{min} < X < x_{max} | room_i)\cdot\mathbb{P}(room_i)}" /></a>
