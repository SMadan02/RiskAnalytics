package com.riskengine.producer;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling // Enable scheduling to allow for periodic tasks, such as simulating market data generation at regular intervals
public class MarketDataProducerApplication {

	public static void main(String[] args) {
		SpringApplication.run(MarketDataProducerApplication.class, args);
	}
	

}