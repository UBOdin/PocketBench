

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
public class SpotifyTest {

    private static final String TEST_PACKAGE = "com.spotify.music";
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
        trace_marker("FLAG123 Start Spotify");
        try {
            // Click minimize screen button:
            Thread.sleep(1000);
            device.click(84, 136);
            // Click search button:
            Thread.sleep(1000);
            device.click(404, 1704);
            // Click textbox:
            Thread.sleep(1000);
            device.click(540,360);
            // Input request:
            type_keys("bach 565");
            // Click first suggestion:
            device.click(619,457);
            // Click play:
            Thread.sleep(1000);
            device.click(985,1557);
            // Let it play:
            Thread.sleep(30 * 1000);
            device.click(985, 1557);

        } catch (Exception e) {
            Log.d(logflag, "Exception Catch:  " + e.toString());
        }
        trace_marker("FLAG123 End Spotify");
        trace_marker("FLAG123 End App Script Test");

    }

    public void type_keys(String inputtext) {

        char char_ascii;

        try {
            for (int i = 0; i < inputtext.length(); i++) {
                char_ascii = inputtext.charAt(i);
                // only supports lower case and space:
                if ((char_ascii >= 'a') && (char_ascii <= 'z')) {
                    //Thread.sleep(500);
                    device.pressKeyCode(char_ascii - 68);
                } else if ((char_ascii >= '0') && (char_ascii <= '9' )) {
                    device.pressKeyCode(char_ascii - 41);
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
