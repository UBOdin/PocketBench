

package com.example.test;

import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
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
public class MetaTest {

    private static final String TEST_PACKAGE = "com.facebook.katana";
    private static final int LAUNCH_TIMEOUT = 20000;
    private static final String STRING_TO_BE_TYPED = "UiAutomator";
    private UiDevice device;
    String logflag = "TESTFLAG";

    static {
        System.loadLibrary("perflib");
    }

    public static native int startcount(int dummy);
    public static native int stopcount(int dummy);

    @Before
    public void startMainActivityFromHomeScreen() {

        trace_marker("FLAG123 Start Home");

        // Initialize UiDevice instance
        device = UiDevice.getInstance(InstrumentationRegistry.getInstrumentation());

        trace_marker("FLAG123 Before Press Home");

        // Start from the home screen
        device.pressHome();

        trace_marker("FLAG123 Before Launcher Wait");

        // Wait for launcher
        final String launcherPackage = device.getLauncherPackageName();
        //assertThat(launcherPackage, notNullValue());
        device.wait(Until.hasObject(By.pkg(launcherPackage).depth(0)),
                LAUNCH_TIMEOUT);

        // Launch the app
        Context context = ApplicationProvider.getApplicationContext();

        final Intent intent = context.getPackageManager()
                .getLaunchIntentForPackage(TEST_PACKAGE);

        //Log.d(logflag, "pointer:  " + intent);
        trace_marker("FLAG123 this??");

        // Clear out any previous instances
        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TASK);
        context.startActivity(intent);

        //Log.d(logflag, "Before");
        trace_marker("FLAG123 Before wait appear");

        // Wait for the app to appear
        device.wait(Until.hasObject(By.pkg(TEST_PACKAGE).depth(0)),
                LAUNCH_TIMEOUT);

        //Log.d(logflag, "After");
        trace_marker("FLAG123 After wait appear");

    }

    /*
    @Test
    public void RunTest() {
        this.PunchKeys();
    }
    */

    @Test
    public void PunchKeys() {

        trace_marker("FLAG123 Start App Script test");
        trace_marker("FLAG123 Start FB");
        try {
            // Navigate to friends list:
            Thread.sleep(1000);
            device.click(450, 237);
            Thread.sleep(1000);
//            device.click(490, 370);
//            Thread.sleep(1000);
            device.swipe(500, 1200, 500, 800, 10);
            // Scroll through friends list:
            Thread.sleep(500);
            for (int i = 0; i < 5; i++) {
                device.swipe(500, 1200, 500, 800, 10);
                Thread.sleep(500);
            }
            // Go back to app home:
            Thread.sleep(500);
            device.pressBack();
//            Thread.sleep(500);
//            device.pressBack();
            Thread.sleep(500);
            // Scroll through feed:
            for (int i = 0; i < 20; i++) {
                device.swipe(500, 1300, 500, 600, 10);
                Thread.sleep(500);
            }
        } catch (Exception e) {
            Log.d(logflag, "Exception Catch:  " + e.toString());
        }
        trace_marker("FLAG123 End FB");
        trace_marker("FLAG123 End App Script Test");

    }

    public void trace_marker(String logtext) {

        Log.d(logflag, logtext);

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