package com.recapify.llm.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;

public record Chunk(
        @JsonProperty("chunk_number") int chunkNumber,
        String title,
        String summary,
        @JsonProperty("key_events") List<String> keyEvents,
        List<String> characters) {
}
