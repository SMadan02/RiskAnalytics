package com.riskengine.producer.service;

import java.util.HashMap;
import java.util.Map;
import java.util.Random;

import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import com.riskengine.producer.model.MarketData;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@Service
public class MarketDataSimulator {
    
    private final MarketDataProducer producer;// Placeholder for actual producer injection    
    private final Map<String, Double> currentPrices = new HashMap<>();
    private final Random random = new Random();

    public MarketDataSimulator(MarketDataProducer producer) {
        this.producer = producer;
        
        // Initialize the market
        currentPrices.put("AAPL", 185.00);
        currentPrices.put("GOOGL", 145.00);
        currentPrices.put("MSFT", 405.00);
        currentPrices.put("TSLA", 175.00);
        currentPrices.put("AMZN", 135.00);
    }


    @Scheduled(fixedRate = 5000)  // Run every 5000ms (5 seconds)
    // The @ConditionalOnProperty annotation ensures that this method only runs if the specified property is set to true in the application configuration
    @ConditionalOnProperty(name = "app.simulator.enabled", havingValue = "true", matchIfMissing = true)
    // It runs every 5 seconds, as specified by the @Scheduled annotation. The method is automatically called by Spring's scheduling mechanism, so you don't need to call it manually. 
    // Just make sure that the application has scheduling enabled (e.g., by adding @EnableScheduling to a configuration class) and that the property app.simulator.enabled is set to true in your application properties or YAML file.
    public void generateMarketData() {
        currentPrices.forEach((symbol, lastPrice) -> {
            // 1. Calculate Random Walk (±1% movement)
            double changePercent = (random.nextDouble() * 0.02) - 0.01;
            double newPrice = lastPrice * (1 + changePercent);

            // 2. Update the map so the next "tick" starts from this new price
            currentPrices.put(symbol, newPrice);

            // 3. Create the Data Object
            MarketData data = new MarketData(
                symbol,
                newPrice,
                java.time.Instant.now().toString(),
                (long) (random.nextInt(5000) + 500) // Random volume
            );

            // 4. Send to Kafka
            producer.sendMarketData(data);
            log.info("Generated: {} @ ${}", symbol, String.format("%.2f", newPrice));
        });
    }
}
