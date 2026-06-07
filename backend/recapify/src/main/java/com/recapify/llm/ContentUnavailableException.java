package com.recapify.llm;

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
}
