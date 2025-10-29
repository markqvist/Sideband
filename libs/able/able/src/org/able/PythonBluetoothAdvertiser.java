package org.able;

import android.bluetooth.le.AdvertisingSet;

interface PythonBluetoothAdvertiser
{
        public void on_advertising_started(AdvertisingSet advertisingSet, int txPower, int status);
        public void on_advertising_stopped(AdvertisingSet advertisingSet);
        public void on_advertising_enabled(AdvertisingSet advertisingSet, boolean enable, int status);
        public void on_advertising_data_set(AdvertisingSet advertisingSet, int status);
        public void on_scan_response_data_set(AdvertisingSet advertisingSet, int status);
        public void on_advertising_parameters_updated(AdvertisingSet advertisingSet, int txPower, int status);
}
