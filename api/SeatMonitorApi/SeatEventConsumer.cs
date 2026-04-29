using System.Text.Json;
using RabbitMQ.Client;
using RabbitMQ.Client.Events;

namespace SeatMonitorApi;

public class SeatEventConsumer(SeatEventBus bus) : BackgroundService
{
    private readonly JsonSerializerOptions _serializerOptions = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower
    };

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        ConnectionFactory factory = new ConnectionFactory { HostName = "localhost" };

        await using IConnection connection = await factory.CreateConnectionAsync(stoppingToken);

        await using IChannel channel = await connection.CreateChannelAsync(cancellationToken: stoppingToken);

        await channel.QueueDeclareAsync(
            "passenger-seat", durable: true, exclusive: false, autoDelete: false,
            arguments: new Dictionary<string, object?> { { "x-queue-type", "quorum" } },
            cancellationToken: stoppingToken);

        AsyncEventingBasicConsumer consumer = new AsyncEventingBasicConsumer(channel);

        consumer.ReceivedAsync += (_, ea) =>
        {
            byte[] body = ea.Body.ToArray();

            if (JsonSerializer.Deserialize<SeatEvent>(body, _serializerOptions) is { } seatEvent)
            {
                bus.Publish(seatEvent);
            }

            return Task.CompletedTask;
        };

        await channel.BasicConsumeAsync("passenger-seat", autoAck: true, consumer: consumer, stoppingToken);

        await Task.Delay(Timeout.Infinite, stoppingToken);
    }
}