# DataURITool

This is a prototype of a package implemented during [Live Stream #59](https://youtu.be/LNQl3_cSsk4)
on my [secondary channel on YouTube](https://www.youtube.com/c/TerenceMartinLive),
and currently does two things.

While viewing any file (including images), the `DataURITool: Copy Data URI to
clipboard` command in the command palette will convert the file into a Data URI
and copy it to the clipboard.

While viewing an HTML or JavaScript file (or other file types; this is
configurable), hovering the mouse over a `data:` URI that represents an image
will show you the image in a hover popup.

This is not a full fledged package (in that there's much more that it could
eventually do), but what's here should work.

The package includes a sample HTML file you can open for testing, as well as a
sample image you can open to invoke the took, because they were used for
testing in the original stream.

This requires a build of Sublime Text >= 4050 (possibly higher; but basically
this will not work in Sublime Text 3) due to using Python 3.8 and some new API
endpoints not available in older versions.
