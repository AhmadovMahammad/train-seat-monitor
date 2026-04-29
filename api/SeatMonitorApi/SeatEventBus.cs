using System.Threading.Channels;

namespace SeatMonitorApi;

public sealed class SeatEventBus
{
    private readonly List<ChannelWriter<SeatEvent>> _channelWriters = [];

    private readonly object _lock = new();

    public IDisposable Subscribe(out ChannelReader<SeatEvent> channelReader)
    {
        Channel<SeatEvent> channel = Channel.CreateBounded<SeatEvent>(new BoundedChannelOptions(100)
        {
            FullMode = BoundedChannelFullMode.DropOldest
        });

        channelReader = channel.Reader;

        lock (_lock)
        {
            _channelWriters.Add(channel.Writer);
        }

        return new DisposableSubscriber(() =>
        {
            lock (_lock)
            {
                _channelWriters.Remove(channel.Writer);
            }

            channel.Writer.TryComplete();
        });
    }

    public void Publish(SeatEvent seatEvent)
    {
        lock (_lock)
        {
            foreach (ChannelWriter<SeatEvent> channelWriter in _channelWriters)
            {
                channelWriter.TryWrite(seatEvent);
            }
        }
    }

    private sealed class DisposableSubscriber(Action dispose) : IDisposable
    {
        public void Dispose()
        {
            dispose.Invoke();
        }
    }
}