package com.riskengine.producer.model;

import lombok.Value;

@Value // This handles private, final, getters, and a constructor all at once
// Define the MarketData class with the specified fields, DTO style for immutability and ease of use in serialization
// Double and Long are used instead of primitive types to allow for null values if needed
public class MarketData {
    String symbol; // Stock symbol, e.g., "AAPL"
    Double price; // Stock price, using Double to allow for null values if necessary
    String timestamp; // ISO 8601 format best for serialization
    Long volume; // Trading volume, using Long to allow for null values if necessary
}
