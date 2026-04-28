using System.Text;
using RabbitMQ.Client;
using RabbitMQ.Client.Events;

namespace SeatMonitorApi;

public class SeatEventConsumer : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        ConnectionFactory connectionFactory = new ConnectionFactory
        {
            HostName = "localhost"
        };

        await using IConnection connection = await connectionFactory.CreateConnectionAsync(stoppingToken);

        await using IChannel channel = await connection.CreateChannelAsync(cancellationToken: stoppingToken);

        await channel.QueueDeclareAsync(
            "passenger-seat", durable: true, exclusive: false, autoDelete: false,
            arguments: new Dictionary<string, object?> { { "x-queue-type", "quorum" } },
            cancellationToken: stoppingToken);

        AsyncEventingBasicConsumer consumer = new AsyncEventingBasicConsumer(channel);

        consumer.ReceivedAsync += (_, ea) =>
        {
            byte[] body = ea.Body.ToArray();
            string message = Encoding.UTF8.GetString(body);
            Console.WriteLine($" [x] Received {message}");
            return Task.CompletedTask;
        };

        await channel.BasicConsumeAsync("passenger-seat", autoAck: true, consumer: consumer,
            cancellationToken: stoppingToken);

        await Task.Delay(Timeout.Infinite, stoppingToken);
    }
}