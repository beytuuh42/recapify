package com.recapify.llm;

import com.recapify.llm.client.MlErrorDetail;
import com.recapify.llm.dto.SummaryRequest;

public class ContentUnavailableException extends RuntimeException {

    private final String title;
    private final Integer season;
    private final Integer episode;
    private final String language;

    public ContentUnavailableException(String title, Integer season, Integer episode, String language) {
        super(String.format("No content found for %s S%02dE%02d (%s)", title, season, episode, language));
        this.title = title;
        this.season = season;
        this.episode = episode;
        this.language = language;
    }

    public String title() { return title; }
    public Integer season() { return season; }
    public Integer episode() { return episode; }
    public String language() { return language; }

    public static RuntimeException from(MlErrorDetail detail, SummaryRequest fallback) {
        if (detail != null && "subtitle_not_found".equals(detail.code())) {
            return new ContentUnavailableException(
                    detail.title() != null ? detail.title() : fallback.title(),
                    detail.season() != null ? detail.season() : fallback.season(),
                    detail.episode() != null ? detail.episode() : fallback.episode(),
                    detail.language() != null ? detail.language() : fallback.language()
            );
        }
        return new MlServiceUnavailableException("ML service returned an unexpected error");
    }
}
