using System.Text.Json;
using System.Threading.Channels;
using SeatMonitorApi;

WebApplicationBuilder builder = WebApplication.CreateBuilder(args);

builder.Services.AddSingleton<SeatEventBus>();

builder.Services.AddHostedService<SeatEventConsumer>();

WebApplication app = builder.Build();

app.UseDefaultFiles();

app.UseStaticFiles();

app.MapGet("/api/layout", (IConfiguration config) =>
{
    string path = config["ConfigPath"] ?? Path.Combine(Directory.GetCurrentDirectory(), "..", "..", "config.json");

    JsonElement layout = JsonDocument.Parse(File.ReadAllText(path)).RootElement;

    return Results.Json(layout);
});

JsonSerializerOptions options = new JsonSerializerOptions
{
    PropertyNamingPolicy = JsonNamingPolicy.CamelCase
};

app.MapGet("/events", async (SeatEventBus bus, HttpContext context, CancellationToken cancellationToken) =>
{
    context.Response.ContentType = "text/event-stream";

    using IDisposable subscriber = bus.Subscribe(out ChannelReader<SeatEvent> channelReader);

    await foreach (SeatEvent seatEvent in channelReader.ReadAllAsync(cancellationToken))
    {
        string data = JsonSerializer.Serialize(seatEvent, options);

        await context.Response.WriteAsync($"event: message\ndata: {data}\n\n", cancellationToken: cancellationToken);

        await context.Response.Body.FlushAsync(cancellationToken);
    }
});

app.Run();