// polling interval for all dashboard queries
export const REFRESH_INTERVAL_SECONDS = 300;

// "5m" for whole minutes, otherwise "90s"
export const REFRESH_LABEL =
  REFRESH_INTERVAL_SECONDS % 60 === 0
    ? `${REFRESH_INTERVAL_SECONDS / 60}m`
    : `${REFRESH_INTERVAL_SECONDS}s`;
