package com.riskengine.producer.config;

import java.net.URI;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import com.riskengine.producer.service.MarketDataProducer;
import com.riskengine.producer.service.MarketDataWebSocketClient;

import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Component
public class WebSocketStarter {

    @Value("${app.finnhub.api-key}")
    private String apiKey;

    @Value("#{'${app.stocks}'.split(',')}")
    private String[] stocks;

    @Autowired
    private MarketDataProducer marketDataProducer;

    private MarketDataWebSocketClient client; // Keep a reference to prevent garbage collection

    @PostConstruct
    public void startWebSocket() {
        try {
            log.info("🔧 Starting WebSocket with API key: {}", apiKey.substring(0, 10) + "...");
            String url = "wss://ws.finnhub.io?token=" + apiKey;
            log.info("🔧 Connecting to: {}", url);
            client = new MarketDataWebSocketClient(new URI(url), marketDataProducer, stocks);
            client.connect();
            log.info("🚀 WebSocket connection initiated...");
        } catch (Exception e) {
            log.error("Failed to start WebSocket", e);
        }
    }
}
