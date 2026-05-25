package com.recapify.llm;

public record SummaryRequest(String title, String media_type, int season, int episode, String language) {
}
