**Program to count video views with concurrent clicks in mind**

This program uses Redis db to store videos, their view count, users, which user watched which video, when it was watched.

Redis db features allow the code to be robust in a situation where multiple users clicked to watch the same video and the same time and the view counter works as expected without any anomalies.
