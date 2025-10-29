package org.able;

import android.bluetooth.le.AdvertisingSet;
import android.bluetooth.le.AdvertisingSetCallback;
import org.able.PythonBluetoothAdvertiser;
import android.util.Log;


public class BLEAdvertiser {
        private String TAG = "BLE-python";
        private PythonBluetoothAdvertiser mPython;
        public AdvertisingSetCallback mCallbackSet;

        public BLEAdvertiser(PythonBluetoothAdvertiser python) {
                mPython = python;
        }

        public AdvertisingSetCallback createCallback() {
                mCallbackSet = new AdvertisingSetCallback() {
                        @Override
                        public void onAdvertisingSetStarted(AdvertisingSet advertisingSet, int txPower, int status) {
                                Log.d(TAG, "onAdvertisingSetStarted, status:" + status);
                                mPython.on_advertising_started(advertisingSet, txPower, status);
                        }

                        @Override
                        public void onAdvertisingSetStopped(AdvertisingSet advertisingSet) {
                                Log.d(TAG, "onAdvertisingSetStopped");
                                mCallbackSet = null;
                                mPython.on_advertising_stopped(advertisingSet);
                        }


                        @Override
                        public void onAdvertisingEnabled(AdvertisingSet advertisingSet, boolean enable, int status) {
                                Log.d(TAG, "onAdvertisingEnabled, enable:" + enable + "status:" + status);
                                mPython.on_advertising_enabled(advertisingSet, enable, status);
                        }


                        @Override
                        public void onAdvertisingDataSet(AdvertisingSet advertisingSet, int status) {
                                Log.d(TAG, "onAdvertisingDataSet, status:" + status);
                                mPython.on_advertising_data_set(advertisingSet, status);
                        }

                        @Override
                        public void onScanResponseDataSet(AdvertisingSet advertisingSet, int status) {
                                Log.d(TAG, "onScanResponseDataSet, status:" + status);
                                mPython.on_scan_response_data_set(advertisingSet, status);
                        }

                        @Override
                        public void onAdvertisingParametersUpdated(AdvertisingSet advertisingSet, int txPower, int status) {
                                Log.d(TAG, "onAdvertisingParametersUpdated, status:" + status);
                                mPython.on_advertising_parameters_updated(advertisingSet, txPower, status);
                        }
                };
                return mCallbackSet;
        }
}
