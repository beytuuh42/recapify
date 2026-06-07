package com.recapify.llm.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public record SummaryRequest(
        String title,
        @JsonProperty("media_type") String mediaType,
        Integer season,
        Integer episode,
        String language) {
}
