from datetime import datetime, timedelta, timezone

from .recording import Recording


class TestDevice:
    def __init__(self, devicename, deviceapi, helper):
        self._deviceapi = deviceapi
        self.devicename = devicename
        self._helper = helper
        self._id = None

    def get_id(self):
        if self._id is None:
            self._id = self._helper.admin_user().get_device_id(self.devicename)
        return self._id

    def has_recording(self):
        self._print_description("    and '{}' has a recording ".format(self.devicename))
        return self.upload_recording()

    def has_audio_recording(self):
        self._print_description(
            "    and '{}' has an audio recording ".format(self.devicename)
        )
        return self.upload_audio_recording()

    def upload_recording(self, properties=None):
        props = self.get_new_recording_props()
        if properties:
            props.update(properties)
        filename = "files/small.cptv"
        recording_id = self._deviceapi.upload_recording(filename, props)

        # Expect to see this in data returned by the API server.
        props["rawMimeType"] = "application/x-cptv"

        return Recording(recording_id, props, filename)

    def get_new_recording_props(self):
        return {
            "type": "thermalRaw",
            "recordingDateTime": _new_timestamp().isoformat(),
            "duration": 10,
            "comment": "hmmm",
            "batteryLevel": 98,
            "batteryCharging": "CHARGING",
            "airplaneModeOn": False,
            "version": "223",
            "additionalMetadata": {"bar": "foo"},
        }

    def upload_audio_recording(self):
        ts = _new_timestamp()
        props = {
            "recordingDateTime": ts.isoformat(),
            "recordingTime": ts.strftime("%H:%M:%S"),
            "duration": 2,
            "batteryLevel": 99,
            "batteryCharging": "FULL",
            "airplaneModeOn": False,
            "relativeToDawn": 9877,
            "relativeToDusk": -6543,
            "version": "123",
            "additionalMetadata": {"foo": "bar"},
        }
        filename = "files/small.mp3"
        recording_id = self._deviceapi.upload_audio_recording(filename, props)
        return Recording(recording_id, props, filename)

    def _print_description(self, description):
        print(description, end="")

    def record_event(self, type_, details, times=None):
        count, detailsId = self._deviceapi.record_event(type_, details, times)
        assert count == 1
        return detailsId

    def record_three_events_at_once(self, detailId):
        print("    which has three events uploaded with detail id {}.".format(detailId))
        now = datetime.now()
        times = [now, now - timedelta(seconds=2), now - timedelta(seconds=4)]
        eventsAdded, detailsId = self._deviceapi.record_event_from_id(detailId, times)

        print("Then three events should have been recorded.")
        assert eventsAdded == 3
        return detailsId

    def download_audio_bait(self, file_id):
        return self._deviceapi.download_file(file_id)

    def get_audio_schedule(self):
        return self._deviceapi.get_audio_schedule()


def _new_timestamp():
    return datetime.now(timezone.utc)
