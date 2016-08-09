ADB=/home/kpd/.buildozer/android/platform/android-sdk-20/platform-tools/adb

go:
	buildozer --verbose android debug deploy run

run:
	buildozer android deploy run

log:
	$(ADB) logcat | grep `$(ADB) shell ps | grep com.powertwenty | cut -c10-15`

