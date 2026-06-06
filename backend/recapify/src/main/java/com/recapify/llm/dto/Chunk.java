package com.recapify.llm.dto;

import java.util.List;

public record Chunk(int chunk_number, String title, String summary, List<String> key_events, List<String> characters) {
}
