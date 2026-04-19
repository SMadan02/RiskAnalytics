package com.riskengine.producer.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
// This class is responsible for configuring Kafka producer settings in the Spring application context
// It uses the @Value annotation to inject the Kafka topic name from the application properties
public class KafkaProducerConfig {

    @Value("${app.kafka.topic}")
    private String topicName;

    /**
     * Provides the Kafka topic name from application properties to be injected
     * into services that need to publish messages.
     *
     * @return configured Kafka topic name
     */
    @Bean
    public String kafkaTopic() {
        return topicName;
    }
}
