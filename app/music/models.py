import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


def less_than_five(value):
    """Raire an error if the value is 5 or greater."""
    if value >= 5:
        raise ValidationError("The price must be lower than 5 euros.")


def get_current_year():
    """Return the current year."""
    return datetime.datetime.today().year


class ValidatedModel(models.Model):
    """Automatically validate the model."""

    def save(self, *args, **kwargs):
        """Call validation on save."""
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        """Metadata."""

        abstract = True


class Author(ValidatedModel):
    """The Author model."""

    name = models.CharField(max_length=255)
    website = models.URLField(null=True, blank=True)
    first_appearance = models.SmallIntegerField(
        null=True, blank=True, verbose_name="Year of first appearance",
        validators=[MinValueValidator(1000), MaxValueValidator(get_current_year)]
    )
    last_appearance = models.SmallIntegerField(
        null=True, blank=True, verbose_name="Year of last appearance",
        validators=[MinValueValidator(1000), MaxValueValidator(get_current_year)]
    )

    def clean(self):
        """Validate the object."""
        if (self.first_appearance and self.last_appearance
                and self.first_appearance > self.last_appearance):
            raise ValidationError("The year of first appearance must be equal or "
                                  "lower to the year of last appearance.")


class Musician(ValidatedModel):
    """The Musician model."""

    INSTRUMENTS = (
        ("piano", "Piano"),
        ("eguitar", "Electric Guitar"),
        ("cguitar", "Classical Guitar"),
        ("aguitar", "Acoustic Guitar"),
        ("ebass", "Electric Bass"),
        ("bass", "Bass"),
        ("drums", "Drums"),
        ("voice", "Voice"),
        ("violin", "Violin"),
        ("harp", "Harp"),
        ("handpan", "Handpan"),
        ("tambourine", "Tambourine"),
        ("sax", "Saxophone"),
        ("trumpet", "Trumpet"),
        ("trombone", "Trombone"),
        ("flute", "Flute"),
        ("clarinet", "Clarinet"),
        ("ukulele", "Ukulele"),
    )

    name = models.CharField(max_length=150)
    nationality = models.CharField(max_length=2)
    instrument = models.CharField(max_length=25, choices=INSTRUMENTS)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    authors = models.ManyToManyField(to=Author, through='RelationshipAuthorMusician', related_name='authors')


class Album(ValidatedModel):
    """The Album model."""

    title = models.CharField(max_length=255)
    year_of_release = models.SmallIntegerField(
        validators=[MinValueValidator(1000), MaxValueValidator(get_current_year)]
    )
    produced_by = models.CharField(max_length=255, null=True, blank=True)


class Song(ValidatedModel):
    """The Song model."""

    STYLES = (
        ("Indie", "Indie"),
        ("Pop", "Pop"),
        ("Rock", "Rock"),
        ("Funky", "Funky"),
        ("Reggaeton", "Reggaeton"),
        ("Classic", "Classic"),
        ("Orquestra", "Orquestra"),
        ("Folk", "Folk")
    )

    audio = models.FileField(upload_to="audio")
    title = models.CharField(max_length=250)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL,
                               db_index=True, null=True, blank=True)
    album = models.ForeignKey(Album, on_delete=models.CASCADE,
                              max_length=250, null=True, blank=True)
    duration = models.DurationField()
    style = models.CharField(max_length=20, choices=STYLES, null=True, blank=True)
    playbacks = models.PositiveIntegerField(null=True, blank=True)
    price = models.DecimalField(decimal_places=2, max_digits=4, default=0,
                                validators=[less_than_five])
    deal_of_the_day = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name="songs_created")
    last_modified = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                         null=True, blank=True, related_name="songs_last_modified")
    authors = models.ManyToManyField(to=Author, through='RelationshipAuthorSong', related_name='song_authors')

    class Meta:
        """Metadata."""

        constraints = [
            models.UniqueConstraint(fields=["title", "author", "album", "duration"],
                                    name="unique_song")
        ]


class Profile(ValidatedModel):
    """A user profile."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    daily_start_time = models.TimeField(default="09:00:00")
    daily_finish_time = models.TimeField(default="14:00:00")
    preferred_style = models.CharField(max_length=30, choices=Song.STYLES)
    preferred_song = models.ForeignKey(Song, on_delete=models.SET_NULL,
                                       null=True, blank=True)


class RelationshipAuthorMusician(ValidatedModel):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="members")
    musician = models.ForeignKey(Musician, on_delete=models.CASCADE)
    start = models.SmallIntegerField(null=True, blank=True)
    end = models.SmallIntegerField(null=True, blank=True)
    

class RelationshipAuthorSong(ValidatedModel):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="song_to_author")
    song= models.ForeignKey(Song, on_delete=models.CASCADE, related_name="author_to_song")

# Task2

"""
1.
In [3]: song_15 = Song.objects.get(pk=15)

In [4]: song_15.authors.add(30, 40)

In [5]: Song.objects.get(pk=15).authors.all()
Out[5]: <QuerySet [<Author: Author object (30)>, <Author: Author object (40)>]>
"""

"""
2.

In [6]: author_50 = Author.objects.get(pk=50)

In [7]: author_50.song_authors.add(10,20,30,40)

In [12]: Author.objects.get(pk=50).song_authors.all()

Out[12]: <QuerySet [<Song: Song object (10)>, <Song: Song object (20)>, <Song: Song object (30)>, <Song: Song object (40)>]>

"""

"""
3.

In [2]: author_100 = Author.objects.get(pk=100)

In [3]: author_100.authors.add(10,20,30,40)

In [4]: Author.objects.get(pk=100).authors.all()

Out[4]: <QuerySet [<Musician: Musician object (10)>, <Musician: Musician object (20)>, <Musician: Musician object (30)>, <Musician: Musician object (40)>]>


"""

"""
4.

In [7]: musicians = Musician.objects.filter(authors__id = 100).values('name','instrument')

In [8]: musicians

Out[8]: <QuerySet [{'name': 'Noah Garcia', 'instrument': 'clarinet'}, {'name': 'Loretta Schumacher', 'instrument': 'eguitar'}, {'name': 'Liam Perez', 'instrument': 'piano'}, {'name': 'Arnold Hutticher', 'instrument': 'trombone'}]>

"""