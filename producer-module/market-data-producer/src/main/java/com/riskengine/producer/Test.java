package com.riskengine.producer;
import com.riskengine.producer.model.MarketData;
public class Test {
    
    public static void example(){
		// Example usage of MarketData class
		MarketData data = new MarketData("AAPL", 150.25, "2024-06-01T12:00:00Z", 1000L);
		System.out.println(data.toString());
	} 
    public static void main(String[] args) {
        example();
    }
    
}
