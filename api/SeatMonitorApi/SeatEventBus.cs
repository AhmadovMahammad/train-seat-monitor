using System.Threading.Channels;

namespace SeatMonitorApi;

public sealed class SeatEventBus
{
    private readonly List<ChannelWriter<SeatEvent>> _writers = [];

    private readonly object _lock = new();

    public IDisposable Subscribe(out ChannelReader<SeatEvent> reader)
    {
        Channel<SeatEvent> channel = Channel.CreateBounded<SeatEvent>(new BoundedChannelOptions(100)
        {
            FullMode = BoundedChannelFullMode.DropOldest
        });

        reader = channel.Reader;

        lock (_lock)
        {
            _writers.Add(channel.Writer);
        }

        return new DisposableUnsubscriber(() =>
        {
            lock (_lock)
            {
                _writers.Remove(channel.Writer);
            }

            channel.Writer.Complete();
        });
    }

    public void Publish(SeatEvent seatEvent)
    {
        lock (_lock)
        {
            foreach (ChannelWriter<SeatEvent> w in _writers)
            {
                w.TryWrite(seatEvent);
            }
        }
    }

    private sealed class DisposableUnsubscriber(Action dispose) : IDisposable
    {
        public void Dispose()
        {
            dispose.Invoke();
        }
    }
}