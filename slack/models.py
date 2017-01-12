from django.db import models

# Create your models here.
class SlackUser(models.Model):
    raw_id = models.CharField(max_length = 255, primary_key=True)
    display = models.CharField(max_length = 255)
    def __str__(self):
        return self.raw_id

class Event(models.Model):
    type = models.CharField(max_length = 255)
    subtype = models.CharField(max_length = 255,null=True)
    ts = models.DateField(auto_now_add=True)
    raw = models.TextField()
    user = models.ForeignKey(SlackUser, null=True)
    def __str__(self):
        return self.type

class Message(models.Model):
    event = models.ForeignKey(Event)
    text = models.TextField()
    def __str__(self):
        return '{user}: {message}'.format(user = self.event.user, message = self.text)
