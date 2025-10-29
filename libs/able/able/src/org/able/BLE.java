package org.able;

import android.app.Activity;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.pm.PackageManager;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothManager;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothProfile;
import android.bluetooth.BluetoothGatt;
import android.bluetooth.BluetoothGattCallback;
import android.bluetooth.BluetoothGattCharacteristic;
import android.bluetooth.BluetoothGattDescriptor;
import android.bluetooth.BluetoothGattService;
import android.bluetooth.le.BluetoothLeScanner;
import android.bluetooth.le.ScanCallback;
import android.bluetooth.le.ScanResult;

import android.bluetooth.le.ScanFilter;
import android.bluetooth.le.ScanSettings;

import android.os.Handler;
import android.util.Log;
import java.util.List;
import org.kivy.android.PythonActivity;
import org.kivy.android.PythonService;
import org.able.PythonBluetooth;


public class BLE {
        private String TAG = "BLE-python";
        private PythonBluetooth mPython;
        private Context mContext;
        private BluetoothAdapter mBluetoothAdapter;
        private BluetoothLeScanner mBluetoothLeScanner;
        private BluetoothGatt mBluetoothGatt;
        private List<BluetoothGattService> mBluetoothGattServices;
        private boolean mScanning;
        private boolean mIsServiceContext = false;

        public void showError(final String msg) {
                Log.e(TAG, msg);
                if (!mIsServiceContext) { PythonActivity.mActivity.toastError(TAG + " error. " + msg); }
                mPython.on_error(msg);
        }

        public BLE(PythonBluetooth python) {
                mPython = python;
                mContext = (Context) PythonActivity.mActivity;
                mBluetoothGatt = null;

                if (mContext == null) {
                        Log.d(TAG, "Service context detected");
                        mIsServiceContext = true;
                        mContext = (Context) PythonService.mService;
                }

                if (!mContext.getPackageManager().hasSystemFeature(PackageManager.FEATURE_BLUETOOTH_LE)) {
                        showError("Device does not support Bluetooth Low Energy.");
                        return;
                }

                final BluetoothManager bluetoothManager =
                        (BluetoothManager) mContext.getSystemService(Context.BLUETOOTH_SERVICE);
                mBluetoothAdapter = bluetoothManager.getAdapter();
                mContext.registerReceiver(mReceiver, new IntentFilter(BluetoothAdapter.ACTION_STATE_CHANGED));
        }

        public BluetoothAdapter getAdapter(int EnableBtCode) {
                if (mBluetoothAdapter == null) {
                        showError("Device do not support Bluetooth Low Energy.");
                        return null;
                }
                if (!mBluetoothAdapter.isEnabled()) {
                        if (mIsServiceContext) {
                                showError("BLE adapter is not enabled");
                        } else {
                                Log.d(TAG, "BLE adapter is not enabled");
                                Intent enableBtIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
                                PythonActivity.mActivity.startActivityForResult(enableBtIntent, EnableBtCode);
                        }
                        return null;
                }
                return mBluetoothAdapter;
        }

        public BluetoothGatt getGatt() {
                return mBluetoothGatt;
        }

        public void startScan(int EnableBtCode,
                              List<ScanFilter> filters,
                              ScanSettings settings) {
                Log.d(TAG, "startScan");
                BluetoothAdapter adapter = getAdapter(EnableBtCode);
                if (adapter != null) {
                    Log.d(TAG, "BLE adapter is ready for scan");
                    if (mBluetoothLeScanner == null) {
                            mBluetoothLeScanner = adapter.getBluetoothLeScanner();
                    }
                    if (mBluetoothLeScanner != null) {
                            mScanning = false;
                            mBluetoothLeScanner.startScan(filters, settings, mScanCallback);
                    } else {
                            showError("Could not get BLE Scanner object.");
                            mPython.on_scan_started(false);
                    }
                }
        }

        public void stopScan() {
                if (mBluetoothLeScanner != null) {
                        Log.d(TAG, "stopScan");
                        mBluetoothLeScanner.stopScan(mScanCallback);
                        if (mScanning) {
                                mScanning = false;
                                mPython.on_scan_completed();
                        }
                }
        }

        private final ScanCallback mScanCallback =
                new ScanCallback() {
                        @Override
                        public void onScanResult(final int callbackType, final ScanResult result) {
                                if (!mScanning) {
                                        mScanning = true;
                                        Log.d(TAG, "BLE scan started successfully");
                                        mPython.on_scan_started(true);
                                }
                                if (mIsServiceContext) {
                                        mPython.on_scan_result(result);
                                        return;
                                }
                                PythonActivity.mActivity.runOnUiThread(new Runnable() {
                                                @Override
                                                public void run() {
                                                        mPython.on_scan_result(result);
                                                }
                                        });
                        }

                        @Override
                        public void onBatchScanResults(List<ScanResult> results) {
                                Log.d(TAG, "onBatchScanResults");
                        }

                        @Override
                        public void onScanFailed(int errorCode) {
                                Log.e(TAG, "BLE Scan failed, error code:" + errorCode);
                                mPython.on_scan_started(false);
                        }
                };

        public void connectGatt(BluetoothDevice device) {
                connectGatt(device, false);
        }

        public void connectGatt(BluetoothDevice device, boolean autoConnect) {
                Log.d(TAG, "connectGatt");
                if (mBluetoothGatt == null) {
                        mBluetoothGatt = device.connectGatt(mContext, autoConnect, mGattCallback, BluetoothDevice.TRANSPORT_LE);
                } else {
                        Log.d(TAG, "BluetoothGatt object exists, use either closeGatt() to close Gatt or BluetoothGatt.connect() to re-connect");
                }
        }

        public void closeGatt() {
                Log.d(TAG, "closeGatt");
                if (mBluetoothGatt != null) {
                        mBluetoothGatt.close();
                        mBluetoothGatt = null;
                }
        }

        private final BroadcastReceiver mReceiver = new BroadcastReceiver() {
                @Override
                public void onReceive(Context context, Intent intent) {
                String action = intent.getAction();
                if (BluetoothAdapter.ACTION_STATE_CHANGED.equals(action)) {
                        Log.d(TAG, "onReceive - BluetoothAdapter state changed");
                        int state = intent.getIntExtra(BluetoothAdapter.EXTRA_STATE, -1);
                        mPython.on_bluetooth_adapter_state_change(state);
                }
                }
        };

        private final BluetoothGattCallback mGattCallback =
                new BluetoothGattCallback() {
                        @Override
                        public void onConnectionStateChange(BluetoothGatt gatt, int status, int newState) {
                                if (newState == BluetoothProfile.STATE_CONNECTED) {
                                        Log.d(TAG, "Connected to GATT server, status:" + status);
                                } else if (newState == BluetoothProfile.STATE_DISCONNECTED) {
                                        Log.d(TAG, "Disconnected from GATT server, status:" + status);
                                }
                                if (mBluetoothGatt == null) {
                                        mBluetoothGatt = gatt;
                                }
                                mPython.on_connection_state_change(status, newState);
                        }

                        @Override
                        public void onServicesDiscovered(BluetoothGatt gatt, int status) {
                                if (status == BluetoothGatt.GATT_SUCCESS) {
                                        Log.d(TAG, "onServicesDiscovered - success");
                                        mBluetoothGattServices = mBluetoothGatt.getServices();
                                } else {
                                        showError("onServicesDiscovered status:" + status);
                                        mBluetoothGattServices = null;
                                }
                                mPython.on_services(status, mBluetoothGattServices);
                        }

                        @Override
                        public void onCharacteristicChanged(BluetoothGatt gatt,
                                                            BluetoothGattCharacteristic characteristic) {
                                mPython.on_characteristic_changed(characteristic);
                        }

                        @Override
                        public void onCharacteristicRead(BluetoothGatt gatt,
                                                         BluetoothGattCharacteristic characteristic,
                                                         int status) {
                                mPython.on_characteristic_read(characteristic, status);
                        }

                        @Override
                        public void onCharacteristicWrite(BluetoothGatt gatt,
                                                          BluetoothGattCharacteristic characteristic,
                                                          int status) {
                                mPython.on_characteristic_write(characteristic, status);
                        }

                        @Override
                        public void onDescriptorRead(BluetoothGatt gatt, 
                                                     BluetoothGattDescriptor descriptor, 
                                                     int status) {
                                mPython.on_descriptor_read(descriptor, status);
                        }

                        @Override
                        public void onDescriptorWrite(BluetoothGatt gatt, 
                                                      BluetoothGattDescriptor descriptor, 
                                                      int status) {
                                mPython.on_descriptor_write(descriptor, status);
                        }

                        @Override
			public void onReadRemoteRssi(BluetoothGatt gatt,
						     int rssi, int status) {
				mPython.on_rssi_updated(rssi, status);
			}

                        @Override
                        public void onMtuChanged(BluetoothGatt gatt,
                                                 int mtu, int status) {
                                Log.d(TAG, String.format("onMtuChanged mtu=%d status=%d", mtu, status));
				mPython.on_mtu_changed(mtu, status);
			}
                };

        public boolean writeCharacteristic(BluetoothGattCharacteristic characteristic, byte[] data, int writeType) {
                if (characteristic.setValue(data)) {
                        if (writeType != 0) {
                                characteristic.setWriteType(writeType);
                        }
                        return mBluetoothGatt.writeCharacteristic(characteristic);
                }
                return false;
        }

        public boolean readCharacteristic(BluetoothGattCharacteristic characteristic) {
                return mBluetoothGatt.readCharacteristic(characteristic);
        }

	public boolean readRemoteRssi() {
		return mBluetoothGatt.readRemoteRssi();
	}
}
