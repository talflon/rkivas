# rkivas
File backupper, especially for media files.
Keeps a copy of all media files it comes across, organized by when they were taken or recorded.
Syncing this to another type of storage can be one-way and write-only, because nothing is ever
changed or deleted.

File names are changed to consist of
- a name for their "source"
  (which could be, for example, the device used to record them)
- when they were recorded
- a lowercase Base32 hash of the file contents.

Because the other information narrows things down significantly,
the hash does not need to be hundreds of bits long.

Files are then organized into directories by things like source, or month taken,
so that individual  directories don't end up with stupendous numbers of files in them.
