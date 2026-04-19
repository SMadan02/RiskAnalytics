package com.riskengine.producer.service;

import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

import com.riskengine.producer.model.MarketData;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Service
@RequiredArgsConstructor // Lombok annotation to generate a constructor for final fields, simplifying dependency injection
public class MarketDataProducer {

    // Inject KafkaTemplate and topic name via constructor injection, leveraging Lombok's @RequiredArgsConstructor for cleaner code
    private final KafkaTemplate<String, MarketData> kafkaTemplate;
    // The topic name is injected from the configuration, allowing for flexibility and separation of concerns
    private final String kafkaTopic;

    /*
    Method to send MarketData to Kafka. 
    It uses the KafkaTemplate to send messages asynchronously and logs the result of the send operation, 
    including success or failure details. We can't just fire-and-forget because we want to log the outcome of the send operation
     */
    public void sendMarketData(MarketData data) {

        if (data == null) {
            log.warn("⚠️ Attempted to send null MarketData. Skipping.");
            return;
        }
        // if (data.getSymbol() == null || data.getPrice() == null || data.getTimestamp() == null || data.getVolume() == null) {
        //     log.warn("⚠️ MarketData has missing fields: {}. Skipping.", data);
        //     return;
        // }
        
        kafkaTemplate.send(kafkaTopic, data.getSymbol(), data)
                .whenComplete((result, ex) -> {
                    if (ex != null) {
                        log.error("❌ Failed to send message for {}: {}", data.getSymbol(), ex.getMessage());
                    } else if (result != null){
                        log.info("✅ Success! Sent {} to Partition: {} with Offset: {}",
                                data.getSymbol(),
                                result.getRecordMetadata().partition(),
                                result.getRecordMetadata().offset());
                    }
                });
    }
}
