using Microsoft.Extensions.DependencyInjection;
using Xunit;

public class MyServiceUnitTest
{
    private ServiceProvider? _serviceProvider;

    public MyServiceUnitTest()
    {
        var serviceCollection = new ServiceCollection();
        serviceCollection.AddSingleton<MyService>();
        _serviceProvider = serviceCollection.BuildServiceProvider();
    }

    [Fact]
    public void TestGetGreetingMethod()
    {
        var myService = _serviceProvider?.GetService<MyService>();
        Assert.NotNull(myService);
        string expected = "Hello, welcome to My Web App!";
        string result = myService!.GetGreeting();
        Assert.Equal(expected, result);
    }

    [Fact]
    public void TestAddMethod()
    {
        var myService = _serviceProvider?.GetService<MyService>();
        Assert.NotNull(myService);
        int expected = 8;
        int result = myService!.Add(5, 3);
        Assert.Equal(expected, result);
    }

    [Fact]
    public void TestSubtractMethod()
    {
        var myService = _serviceProvider?.GetService<MyService>();
        Assert.NotNull(myService);
        int expected = 2;
        int result = myService!.Subtract(5, 3);
        Assert.Equal(expected, result);
    }
}
