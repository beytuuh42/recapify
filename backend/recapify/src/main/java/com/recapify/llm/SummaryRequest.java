package com.recapify.llm;

public record SummaryRequest(String title, String media_type, Integer season, Integer episode, String language) {
}
