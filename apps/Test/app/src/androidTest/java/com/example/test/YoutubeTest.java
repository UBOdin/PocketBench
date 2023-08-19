

package com.example.test;

import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.util.Log;
import android.view.KeyEvent;

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
public class YoutubeTest {

    private static final String TEST_PACKAGE = "com.google.android.youtube";
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
        trace_marker("FLAG123 Start Youtube");
        try {
            // Click search button:
            Thread.sleep(1000);
            device.click(879,126);
            // Click on first suggestion:
            Thread.sleep(2000);
            device.click(550,126); // textbox
            //device.click(472,252);  // first suggestion
            //device.click(472, 378);  //second suggestion

            //device.pressKeyCode(KeyEvent.KEYCODE_C);
            type_keys("we so lit");

            Thread.sleep(20 * 1000);

        } catch (Exception e) {
            Log.d(logflag, "Exception Catch:  " + e.toString());
        }
        trace_marker("FLAG123 End Youtube");
        trace_marker("FLAG123 End App Script Test");

    }

    public void type_keys(String inputtext) {

        char char_ascii;

        try {
            for (int i = 0; i < inputtext.length(); i++) {
                char_ascii = inputtext.charAt(i);
                // only supports lower case and space:
                if ((char_ascii >= 'a') && (char_ascii < 'z')) {
                    //Thread.sleep(500);
                    device.pressKeyCode(char_ascii - 68);
                } else if (char_ascii == ' ') {
                    //Thread.sleep(500);
                    device.pressKeyCode(KeyEvent.KEYCODE_SPACE);
                }
            }
            device.pressKeyCode(KeyEvent.KEYCODE_ENTER);
        } catch (Exception e) {
            Log.d(logflag, "Exception Catch:  " + e.toString());
        }
        return;

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
