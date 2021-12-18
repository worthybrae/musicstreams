# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Albums(models.Model):
    albumspotifyid = models.CharField(db_column='albumSpotifyId', primary_key=True, max_length=200)  # Field name made lowercase.
    albumname = models.CharField(db_column='albumName', max_length=200, blank=True, null=True)  # Field name made lowercase.
    artistname = models.CharField(db_column='artistName', max_length=100, blank=True, null=True)  # Field name made lowercase.
    releasedate = models.DateField(db_column='releaseDate', blank=True, null=True)  # Field name made lowercase.
    coverart = models.CharField(db_column='coverArt', max_length=255, blank=True, null=True)  # Field name made lowercase.
    albumstatus = models.CharField(db_column='albumStatus', max_length=10, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'albums'


class Songstreams(models.Model):
    songspotifyid = models.CharField(db_column='songSpotifyId', max_length=255, blank=True, null=True)  # Field name made lowercase.
    daterecorded = models.DateField(db_column='dateRecorded', blank=True, null=True)  # Field name made lowercase.
    totalstreams = models.BigIntegerField(db_column='totalStreams', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'songStreams'


class Songs(models.Model):
    songspotifyid = models.CharField(db_column='songSpotifyId', primary_key=True, max_length=255)  # Field name made lowercase.
    albumspotifyid = models.CharField(db_column='albumSpotifyId', max_length=255, blank=True, null=True)  # Field name made lowercase.
    songname = models.CharField(db_column='songName', max_length=200, blank=True, null=True)  # Field name made lowercase.
    songduration = models.IntegerField(db_column='songDuration', blank=True, null=True)  # Field name made lowercase.
    songorder = models.IntegerField(db_column='songOrder', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'songs'
