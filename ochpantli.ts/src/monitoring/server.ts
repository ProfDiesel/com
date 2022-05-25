#!/usr/bin/env node

import express from "express";
import {Server, Path, GET } from "typescript-rest";

import { combineReducers, createStore } from '@reduxjs/toolkit'
import { componentListSlice, ComponentListState } from './ComponentListSlice';

const reducer = combineReducers({
  componentList: componentListSlice.reducer,
})

const store = createStore(reducer)

@Path("/components")
class ComponentListService {
  @GET
  getComponentList(): ComponentListState {
    return store.getState().componentList;
  }
}

let app: express.Application = express();
Server.buildServices(app);

app.listen(3000, function() {
  console.log('Rest Server listening on port 3000!');
});
