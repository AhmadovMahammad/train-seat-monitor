namespace SeatMonitorApi;

public record SeatEvent(string TrainId, string WagonId, string CameraId, string SeatId, string Status);
