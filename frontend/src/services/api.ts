// define TS interfaces for PEP data structs
// implement following funcs:
// fetchPeps
// fetchPepByID
// searchPeps
// configure axios base url and error handling

import axios from "axios";

interface PEP {
  //TODO: mock the data structure from the JSON
}
interface PEPListResponse {
  peps: PEP[];
  total: number;
  page: number;
  per_page: number;
}
interface SearchResponse {
  results: PEP[];
  query: string;
  total_matches: number;
}
interface PEPListParams {
  page?: number;
  per_page?: number;
  status?: number;
  type?: string;
}
interface SearchParams {
  q: string;
  page?: number;
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8420/api",
  timeout: 10000, //10 sec
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    //turn errors into component handleable
    if (error.response) {
      throw new Error(
        `API Error: ${error.response.status} - ${error.response.data.message ?? "Unknown error"}`,
      );
    } else if (error.request) {
      throw new Error("Network error - please check your connection");
    } else {
      // Something else
      throw new Error("Request failed");
    }
  },
);
