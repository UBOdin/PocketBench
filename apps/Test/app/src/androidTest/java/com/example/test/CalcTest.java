package com.example.test;

import android.content.Context;
import android.content.Intent;
import android.util.Log;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;

import androidx.test.core.app.ApplicationProvider;
import androidx.test.filters.SdkSuppress;
import androidx.test.platform.app.InstrumentationRegistry;
import androidx.test.runner.AndroidJUnit4;
import androidx.test.uiautomator.UiDevice;
import androidx.test.uiautomator.By;
import androidx.test.uiautomator.UiSelector;
import androidx.test.uiautomator.Until;

import static org.junit.Assert.assertTrue;


@RunWith(AndroidJUnit4.class)
@SdkSuppress(minSdkVersion = 18)
public class CalcTest {

    private static final String TEST_PACKAGE
            //= "com.example.android.testing.uiautomator.BasicSample";
            = "com.google.android.calculator";
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

        Log.d(logflag, "TEST123");

        String prefix = TEST_PACKAGE + ":id/";
        String rid2 = prefix + "digit_2";
        String ridp = prefix + "op_add";
        String rid3 = prefix + "digit_3";
        String ride = prefix + "eq";

        try {
            device.findObject(new UiSelector().packageName(TEST_PACKAGE).resourceId(rid2)).click();
            device.findObject(new UiSelector().packageName(TEST_PACKAGE).resourceId(ridp)).click();
            device.findObject(new UiSelector().packageName(TEST_PACKAGE).resourceId(rid3)).click();
            device.findObject(new UiSelector().packageName(TEST_PACKAGE).resourceId(ride)).click();
        } catch (Exception e) {
            Log.d(logflag, "Exception:  " + e.toString());
        }

        //assertTrue(false);

    }

}




