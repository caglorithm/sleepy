VIEW = {
  "general": {
    "title": "General",
    "content": {
      "checkpoints": {
        "title": "Checkpoints",
        "fields": {
          "useCheckpoints": {
            "title": "Use Checkpoints",
            "fieldType": "bool",
            "default": False
          }
        }
      },
      "windowBar": {
        "title": "Window Bar",
        "fields": {
          "showIndex": {
            "title": "Show index of current event",
            "fieldType": "bool",
            "default": True
          }
        }
      }
    }
  },
  "plot": {
    "title": "Plots",
    "content": {
      "grid": {
        "title": "Grid",
        "fields": {
          "plotGrid": {
            "title": "Plot data on grid",
            "fieldType": "bool",
            "default": True
          },
          "plotGridSize": {
            "title": "Separation of two vertical grid lines in seconds",
            "fieldType": "float",
            "default": 1.15
          }
        }
      },
      "colors": {
        "title": "Colors",
        "fields": {
          "plotLineColor": {
            "title": "Color of the plotted graph",
            "fieldType": "color",
            "default": "#Af77b4"
          },
          "plotSelectedColor": {
            "title": "Color of the selected event",
            "fieldType": "color",
            "default": "#FF7F50"
          },
          "plotUserEventColor": {
            "title": "Color of user events",
            "fieldType": "color",
            "default": "#ABCABC"
          }
        }
      },
      "dimensions": {
        "title": "Dimensions",
        "fields": {
          "pointSize": {
            "title": "Marker size of point event",
            "fieldType": "int",
            "default": 12
          },
          "lineWidth": {
            "title": "Width of line plot",
            "fieldType": "int",
            "default": 2
          }
        }
      }
    }
  },
  "events": {
    "title": "Events",
    "content": {
      "intervals": {
        "title": "Displayed intervals",
        "fields": {
          "intervalMin": {
            "title": "Seconds displayed before event",
            "fieldType": "float",
            "default": 3
          },
          "intervalMax": {
            "title": "Seconds displayed after event",
            "fieldType": "float",
            "default": 3
          }
        }
      },
      "filters": {
        "title": "Filters",
        "fields": {
          "plotFiltered": {
            "title": "Plot filtered data",
            "fieldType": "bool",
            "default": True
          }
        }
      }
    }
  }
}
