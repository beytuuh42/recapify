package com.recapify.llm.dto;

import java.util.List;

public record SummaryResponse(String title, String final_summary, List<String> key_events, List<String> characters,
                              List<Chunk> chunk_summaries) {

}
