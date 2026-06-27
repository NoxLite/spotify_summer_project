from django.db import models

class SpotifyUser(models.Model):
    user_id = models.CharField(max_length=255, primary_key=True)
    age = models.CharField(max_length=50, blank=True, null=True)
    gender = models.CharField(max_length=50, blank=True, null=True)
    subscription_plan = models.CharField(max_length=100, blank=True, null=True)
    registration_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"User {self.user_id} ({self.age}, {self.gender})"


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Artist(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255)
    genres = models.ManyToManyField(Genre, related_name='artists')

    def __str__(self):
        return self.name


class Track(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    # Разрешаем пустые значения, пока не скачаем данные из API
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='tracks', null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)

    tempo = models.FloatField(null=True, blank=True)
    energy = models.FloatField(null=True, blank=True)
    danceability = models.FloatField(null=True, blank=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return str(self.id)


class Listen(models.Model):
    user = models.ForeignKey(SpotifyUser, on_delete=models.CASCADE, related_name='listens')
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='listens')
    listened_at = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=['listened_at']),
            models.Index(fields=['user']),
            models.Index(fields=['track']),
        ]

    def __str__(self):
        return f"{self.user_id} listened to {self.track_id} at {self.listened_at}"
