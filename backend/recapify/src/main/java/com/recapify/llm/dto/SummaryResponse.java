package com.recapify.llm.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;

public record SummaryResponse(
        String title,
        @JsonProperty("final_summary") String finalSummary,
        @JsonProperty("key_events") List<String> keyEvents,
        List<String> characters,
        @JsonProperty("chunk_summaries") List<Chunk> chunkSummaries) {
}
