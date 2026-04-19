package com.riskengine.producer.service;

import java.time.Instant;

import org.java_websocket.client.WebSocketClient;
import org.java_websocket.handshake.ServerHandshake;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.riskengine.producer.model.MarketData;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class MarketDataWebSocketClient extends WebSocketClient {

    private final ObjectMapper mapper = new ObjectMapper();
    private final MarketDataProducer producer;
    private final String[] stocks;

    // Constructor to initialize the WebSocket client with the server URI, producer, and stocks
    // A constructor is a special method in a class that is called when an object of that class is created. 
    // It is used to initialize the object's state and set up any necessary resources. 
    // In this case, the constructor takes a URI as an argument, which is the address of the WebSocket server to connect to. 
    // The constructor then calls the superclass constructor (WebSocketClient) with this URI to establish the connection.
    public MarketDataWebSocketClient(java.net.URI serverUri, MarketDataProducer producer, String[] stocks) {
        super(serverUri);
        this.producer = producer;
        this.stocks = stocks;
    }

    @Override
    // This method is called when the WebSocket connection is opened
    public void onOpen(ServerHandshake handshakedata) {
        log.info("WebSocket opened: " + handshakedata.getHttpStatusMessage());
        for (String stock : stocks) {
            send("{\"type\":\"subscribe\",\"symbol\":\"" + stock + "\"}");
        }
    }

    @Override
    public void onMessage(String message) {
        try {
            JsonNode root = mapper.readTree(message);

            // Check if it's a trade message
            String type = root.get("type").asText();
            if ("ping".equals(type)) {
                send("{\"type\":\"pong\"}");  // Keep connection alive
                return;
            }

            if ("error".equals(type)) {
                log.error("❌ Finnhub error: {}", message);
                return;
            }

            if (!"trade".equals(type)) {
                log.info("Received non-trade message: {}", message);
                return;
            }

            // Loop through all trades in the data array
            JsonNode dataArray = root.get("data");
            for (JsonNode trade : dataArray) {
                String symbol = trade.get("s").asText();
                double price = trade.get("p").asDouble();
                long timestamp = trade.get("t").asLong();
                long volume = trade.get("v").asLong();

                // Convert timestamp to ISO 8601
                String isoTimestamp = Instant.ofEpochMilli(timestamp).toString();

                // Create MarketData
                MarketData marketData = new MarketData(
                        symbol,
                        price,
                        isoTimestamp,
                        volume
                );

                // Send to Kafka
                producer.sendMarketData(marketData);
            }

        } catch (Exception e) {
            log.error("Failed to parse message: {}", message, e);
        }
    }

    @Override
    // This method is called when the WebSocket connection is closed
    public void onClose(int code, String reason, boolean remote) {
        log.info("WebSocket closed: {} - {}", (remote ? "Server Side" : "Client Side"), reason);
    }

    @Override
    // This method is called when an error occurs with the WebSocket
    public void onError(Exception ex) {
        log.error("WebSocket error: {}", ex.getMessage(), ex);
    }

}
