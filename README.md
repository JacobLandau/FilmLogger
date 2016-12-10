# FilmLogger

## Synopsis
FilmLogger is a logging app that creates databases for users based on their moviegoing experiences.
In short, it's a list of each time you go to the movies and what the conditions are. This list provides
data that can be used with analysis engines like the sister project [FilmTrackr](https://github.com/JacobLandau/FilmTrackr).

Prior lists can be opened to update existing lists, or new lists can be created by simply entering your
data. IMDB is cross-referenced to check that the film exists (i.e. a valid entry), and the poster is
displayed as a double-check against reboots/remakes. Input and Output can come in either JSON or YAML format.

## Data Sample
An example of a valid data set is as follows:

    ---
    '1':
      Title: Blarg
      Day: 7
      Month: 11
      Year: 2007
      Theater?: n
    '2':
      Title: Revenge of Blarg
      Day: 11
      Month: 11
      Year: 2007
      Theater?: n
    '3':
      Title: A Film other than Blarg
      Day: 27
      Month: 12
      Year: 2016
      Theater?: y

## Motivation
The idea that science and the humanties are seperate is a falsehood. New technologies provide the means for new expressions.
As someone with an interest in both data science and cinema, the ability to synergize these two interest fields drives me.
Thus, collecting data through FilmLogger, and analyzing data through [FilmTrackr](https://github.com/JacobLandau/FilmTrackr),
in order to provide new insights into how we can tailor film to the trends of human interest.

## Installation
    pip install -r requirements.txt

After that, just run the `logger.py` script inside the folder.

## Contributors

Feel free to send pull requests my way or fire bug reports down the issue tracker.

## License
Usage of this software is granted under the terms of the MIT License. A copy of
this license is included within this repository, and any usage of this software
must follow the terms set out within that license.
