# Stock Watch
This is a simple Kivy application that tracks the latest price of a set of stocks and shows the amount you've gained or lost.   


![Android version screen-shot](screen_shots/20160825.png)



## Platforms
It has been tested on Linux and Android.

##To Build:
In order to build for Android you must enable the CSV library.  Do this by editing each of the following files and removing the line containing _csv:
  1.  ./.buildozer/android/platform/python-for-android/src/blacklist.txt
  2.  ./.buildozer/android/platform/python-for-android/dist/stockwatch/blacklist.txt

Then:
<pre>buildozer --verbose android debug deploy run</pre>



# TODO:
##fix rotation bug
/home/kpd/.buildozer/android/platform/android-sdk-20/platform-tools/adb logcat | grep `/home/kpd/.buildozer/android/platform/android-sdk-20/platform-tools/adb shell ps | grep com.powertwenty | cut -c10-15`
I/ActivityManager(  886): Start proc 16411:com.powertwenty.kivy.stockwatch:python/u0a216 for activity com.powertwenty.kivy.stockwatch/org.renpy.android.PythonActivity
I/python  (16411): [INFO              ] [Android     ] Must go into sleep mode, check the app
I/python  (16411): [INFO              ] [Android     ] App doesn't support pause mode, stop.
I/python  (16411): [INFO              ] [Base        ] Leaving application in progress...
I/python  (16411): Python for android ended.
I/art     (16411): System.exit called, status: 0
I/AndroidRuntime(16411): VM exiting with result code 0, cleanup skipped.
I/ActivityManager(  886): Process com.powertwenty.kivy.stockwatch:python (pid 16411) has died

