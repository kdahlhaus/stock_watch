ADB=/home/kpd/.buildozer/android/platform/android-sdk-20/platform-tools/adb
ZIPALIGN=/home/kpd/.buildozer/android/platform/android-sdk-20/build-tools/24.0.1/zipalign

UNSIGNED=./bin/StockWatch-0.1-release-unsigned.apk
FINAL_RELEASE_APK=./bin/StockWatch-0.1-release.apk

go:
	buildozer --verbose android debug deploy run

run:
	buildozer android deploy run

release:
	echo buildozer android release
	echo jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore stopwatch-release-key.keystore $(UNSIGNED) stopwatch
	$(ZIPALIGN) -v 4 $(UNSIGNED) $(FINAL_RELEASE_APK)


log:
	$(ADB) logcat | grep `$(ADB) shell ps | grep com.powertwenty | cut -c10-15`

