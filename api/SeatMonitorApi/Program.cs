using SeatMonitorApi;

WebApplicationBuilder builder = WebApplication.CreateBuilder(args);

builder.Services.AddHostedService<SeatEventConsumer>();

WebApplication app = builder.Build();

app.UseHttpsRedirection();

app.Map("/info", context =>
{
    context.Response.ContentType = "text/plain";
    return context.Response.WriteAsync("Welcome to Seat Monitor API!");
});

app.Run();