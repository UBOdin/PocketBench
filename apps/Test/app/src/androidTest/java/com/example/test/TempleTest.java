package com.example.test;

import android.content.Context;
import android.content.Intent;
import android.util.Log;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;

import java.io.FileOutputStream;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;

import androidx.test.core.app.ApplicationProvider;
import androidx.test.filters.SdkSuppress;
import androidx.test.platform.app.InstrumentationRegistry;
import androidx.test.runner.AndroidJUnit4;
import androidx.test.uiautomator.UiDevice;
import androidx.test.uiautomator.By;
import androidx.test.uiautomator.UiSelector;
import androidx.test.uiautomator.Until;


@RunWith(AndroidJUnit4.class)
@SdkSuppress(minSdkVersion = 18)
public class TempleTest {

    private static final String TEST_PACKAGE = "com.imangi.templerun2";
    private static final int LAUNCH_TIMEOUT = 5000;
    private static final String STRING_TO_BE_TYPED = "UiAutomator";
    private UiDevice device;
    String logflag = "TESTFLAG";

    @Before
    public void startMainActivityFromHomeScreen() {
        // Initialize UiDevice instance
        device = UiDevice.getInstance(InstrumentationRegistry.getInstrumentation());

        // Start from the home screen
        device.pressHome();

        // Wait for launcher
        final String launcherPackage = device.getLauncherPackageName();
        //assertThat(launcherPackage, notNullValue());
        device.wait(Until.hasObject(By.pkg(launcherPackage).depth(0)),
                LAUNCH_TIMEOUT);

        // Launch the app
        Context context = ApplicationProvider.getApplicationContext();

        final Intent intent = context.getPackageManager()
                .getLaunchIntentForPackage(TEST_PACKAGE);

        Log.d(logflag, "pointer:  " + intent);

        // Clear out any previous instances
        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TASK);
        context.startActivity(intent);

        Log.d(logflag, "Before");

        // Wait for the app to appear
        device.wait(Until.hasObject(By.pkg(TEST_PACKAGE).depth(0)),
                LAUNCH_TIMEOUT);

        Log.d(logflag, "After");

    }

    @Test
    public void PunchKeys() {

        Log.d(logflag, "FLAG123 Start App Script Test");
        trace_marker("FLAG123 Start App Script Test");

        try {
            Thread.sleep(30000);
            Log.d(logflag, "After timeout");
            device.click(530, 1750);
            Log.d(logflag, "After click");
            Thread.sleep(5000);
            device.click(530, 1750);
            Log.d(logflag, "Second click");
/*
            Thread.sleep(7500);
            Log.d(logflag, "before jump 1");
            device.swipe(550, 1700, 550, 1200, 10);
            Thread.sleep(5000);
            Log.d(logflag, "between jumps 1-2");
            device.swipe(550, 1700, 550, 1200, 10);
            Thread.sleep(4000);
            Log.d(logflag, "between jumps 2-3");
            device.swipe(550, 1700, 550, 1200, 10);
*/
            Thread.sleep(7000);

            device.click(930, 1770);  // dummy
            Thread.sleep(5000);

        } catch (Exception e) {
            Log.d(logflag, "Exception Catch:  " + e.toString());
        }
        trace_marker("FLAG123 End App Script Test");

    }

    public void trace_marker(String logtext) {
        PrintWriter outStream = null;
        try {
            FileOutputStream fos = new FileOutputStream("/sys/kernel/debug/tracing/trace_marker");
            outStream = new PrintWriter(new OutputStreamWriter(fos));
            outStream.println(logtext);
            outStream.flush();
        } catch(Exception e) {
            Log.d(logflag, "Exception catch:  " + e.toString());
            return;
        } finally {
            if (outStream != null) {
                outStream.close();
            }
        }
        return;
    }

}




