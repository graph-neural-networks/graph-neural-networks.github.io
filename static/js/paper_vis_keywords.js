let all_papers = [];
const all_pos = [];
const allKeys = {
  authors: [],
  keywords: [],
  titles: [],
};
const filters = {
  authors: null,
  keywords: null,
  title: null,
};

const summaryBy = "keywords"; // or: "abstract"

let currentTippy = null;
const brush = null;
const sizes = {
  margins: { l: 20, b: 20, r: 20, t: 20 },
};

const explain_text_plot = d3.select("#explain_text_plot");
const summary_selection = d3.select("#summary_selection");
const sel_papers = d3.select("#sel_papers");

const persistor = new Persistor("Mini-Conf-Papers");

let trackhighlight = [];
let color;
let opacity;
const plot_size = () => {
  const cont = document.getElementById("container");
  const wh = Math.max(window.innerHeight - 280, 300);
  let ww = Math.max(cont.offsetWidth - 95, 300);
  if (cont.offsetWidth < 768) ww = cont.offsetWidth - 10.0;

  if (wh / ww > 1.3) {
    const min = Math.min(wh, ww);
    return [min, min];
  }
  return [ww, ww];
};

const xS = d3.scaleLinear().range([0, 600]);
const yS = d3.scaleLinear().range([0, 600]);
const plot = d3.select(".plot");

function hexToRgb(hex, alpha) {
  hex = hex.replace("#", "");
  const r = parseInt(
    hex.length === 3 ? hex.slice(0, 1).repeat(2) : hex.slice(0, 2),
    16
  );
  const g = parseInt(
    hex.length === 3 ? hex.slice(1, 2).repeat(2) : hex.slice(2, 4),
    16
  );
  const b = parseInt(
    hex.length === 3 ? hex.slice(2, 3).repeat(2) : hex.slice(4, 6),
    16
  );
  if (alpha) {
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  }
  return `rgb(${r}, ${g}, ${b})`;
}

const tooltip_template = (d) => `
    <div>
        <div class="tt-title">${d.parent.data.name}: ${d.data.name}</div>
     </div>   
`;

function triggerListView(name, allPapers) {
  let all_sel = [];
  if (name === "all") {
    all_sel = allPapers
      .map((e) => e.data.papers)
      .flat()
      .filter((d) => d);
  } else {
    all_sel = allPapers
      .filter((d) => d.data.name === name)
      .map((e) => e.data.papers)
      .flat();
  }
  all_sel = _.uniqWith(all_sel, (a, b) => a.id === b.id && a.track === b.track);

  const sel_papers_selection = d3.select("#sel_papers");
  const authorLimit = 10;
  const keywordLimit = 10;
  sel_papers_selection
    .selectAll(".sel_paper")
    .data(all_sel)
    .join("div")
    .attr("class", "sel_paper")
    .style("background", (d) => {
      return hexToRgb(color(d.track), opacity(5));
    })
    .html(
      (d) =>
        `<div class="p_title">${
          d.title
        }</div> <div class="p_authors">${d.authors
          .slice(0, authorLimit)
          .join(", ")}</div> <div><b>Keywords</b>: ${d.keywords
          .slice(0, keywordLimit)
          .join(", ")} </div>`
    )
    .on("click", (event, d) => window.open(`paper_${d.id}.html`, "_blank"));
}

function treeMap(data) {
  if (data.length > 0) {
    const trackMappings = {};
    data.forEach((e) => {
      if (!(e.content.track in trackMappings)) {
        trackMappings[e.content.track] = {};
      }
      e.content.keywords.forEach((keyword) => {
        const lowerCasedKeyword = keyword
          .toLowerCase()
          .replace(/[.,/#!$%^&*;:{}=\-_`~()]/g, "")
          .replace(/\s{2,}/g, " ");
        if (lowerCasedKeyword in trackMappings[e.content.track]) {
          trackMappings[e.content.track][lowerCasedKeyword].push({
            title: e.content.title,
            image_path: e.card_image_path,
            keywords: e.content.keywords,
            authors: e.content.authors,
            id: e.id,
            track: e.content.track,
          });
        } else {
          trackMappings[e.content.track][lowerCasedKeyword] = [
            {
              title: e.content.title,
              image_path: e.card_image_path,
              keywords: e.content.keywords,
              authors: e.content.authors,
              id: e.id,
              track: e.content.track,
            },
          ];
        }
      });
    });
    // now filter out all track keys with only 1 value
    const filteredTrackMappings = {};
    const funct = data.length < 10 ? (_) => true : ([_, v]) => v.length > 1;
    Object.entries(trackMappings).forEach(([track, keywords]) => {
      filteredTrackMappings[track] = Object.fromEntries(
        Object.entries(keywords).filter(funct)
      );
    });
    const parseTracksToTree = (mappings) => {
      const hierarchalTreeData = { children: [] };
      Object.keys(mappings).forEach((TRACK_KEY) => {
        const children = Object.keys(mappings[TRACK_KEY]).map((KEYWORD_KEY) => {
          return {
            name: KEYWORD_KEY,
            group: KEYWORD_KEY,
            papers: mappings[TRACK_KEY][KEYWORD_KEY],
            value: mappings[TRACK_KEY][KEYWORD_KEY].length,
            colname: "placeholder",
          };
        });

        hierarchalTreeData.children.push({
          name: TRACK_KEY,
          children,
          colname: "placeholder2",
        });
      });
      return hierarchalTreeData;
    };
    const treeData = parseTracksToTree(filteredTrackMappings);
    const root = d3.hierarchy(treeData).sum((d) => d.value);

    d3
      .treemap()
      .size([1000, 1000])
      .paddingTop(24)
      .paddingRight(1)
      .paddingInner(2)(root);
    color = d3
      .scaleOrdinal()
      .domain(Object.keys(trackMappings))
      .range(d3.schemeSet3);
    opacity = d3.scaleLinear().domain([0, 10]).range([0.2, 1]);

    // and to add the text labels
    const is_clicked = false;

    const svg = d3.select("#heatmap");
    svg.selectAll("*").remove();

    svg
      .selectAll("rect")
      .data(root.leaves())
      .enter()
      .append("rect")
      .attr("x", function (d) {
        return d.x0;
      })
      .attr("y", function (d) {
        return d.y0;
      })
      .attr("class", function (d) {
        return `recter keyword-${d.data.name.replace(" ", "")}`;
      })
      .attr("width", function (d) {
        return d.x1 - d.x0;
      })
      .attr("height", function (d) {
        return d.y1 - d.y0;
      })
      .style("stroke", "black")
      .style("fill", function (d) {
        return color(d.parent.data.name);
      })
      .style("opacity", function (d) {
        return opacity(d.data.value);
      })
      .on("click", function (event, d) {
        d3.selectAll(`.recter`)
          .style("fill", (e) => color(e.parent.data.name))
          .style("opacity", (e) => opacity(e.data.value))
          .style("stroke-width", 1);
        d3.selectAll(`.keyword-${d.data.name.replace(" ", "")}`)
          .style("fill", (e) => color(e.parent.data.name))
          .style("opacity", 1)
          .style("stroke-width", 5)
          .style("stroke", "black");
        triggerListView(d.data.name, root.leaves());
      });

    svg
      .selectAll("titles")
      .data(
        root.descendants().filter(function (d) {
          return d.depth === 1;
        })
      )
      .enter()
      .append("text")
      .attr("x", function (d) {
        return d.x0;
      })
      .attr("y", function (d) {
        return d.y0 + 21;
      })
      .attr("class", "titles")
      .text(function (d) {
        const pixelsPerCharacter = 5.5;
        const numCharacters = Math.floor((d.x1 - d.x0) / pixelsPerCharacter);
        if (d.data.name.length > numCharacters) {
          return `${d.data.name.substring(0, numCharacters)}...`;
        }
        return d.data.name;
      })
      .attr("font-size", "11px")
      .attr("fill", "black");
    svg
      .append("text")
      .attr("x", 0)
      .attr("y", 20)
      .text("Keywords by Track")
      .attr("font-size", "19px")
      .attr("fill", "grey");

    currentTippy = tippy(".recter", {
      content(reference) {
        const value = d3.select(reference).datum().name;
        return value;
      },
      onShow(instance) {
        const d = d3.select(instance.reference).datum();
        instance.setContent(tooltip_template(d));
      },

      allowHTML: true,
    });
    currentTippy.forEach((t) => t.enable());
    triggerListView("all", root.leaves());
  }
}

const updateVis = () => {
  const storedPapers = persistor.getAll();
  all_papers.forEach((openreview) => {
    openreview.content.read = storedPapers[openreview.id] || false;
    openreview.content.tracker =
      trackhighlight.includes(openreview.id) || false;
  });
  //   const is_filtered = filters.authors || filters.keywords || filters.titles;
  const is_filtered = filters.keywords;
  const [pW, pH] = plot_size();

  plot.attr("width", pW).attr("height", pH);
  d3.select("#table_info").style("height", `${pH / 3}px`);

  xS.range([sizes.margins.l, pW - sizes.margins.r]);
  yS.range([sizes.margins.t, pH - sizes.margins.b]);
  treeMap(
    all_papers.filter((d) => {
      if ("is_selected" in d) return d.is_selected;
      return true;
    })
  );
};

const render = () => {
  const f_test = [];
  Object.keys(filters).forEach((k) => {
    if (filters[k]) {
      f_test.push([k, filters[k]]);
    }
    // f_test.push([k, filters[k]]) : null;
  });

  let test = (d) => {
    let i = 0;
    let pass_test = true;
    while (i < f_test.length && pass_test) {
      if (f_test[i][0] === "titles") {
        pass_test &= d.content.title === f_test[i][1]; // eslint-disable-line no-bitwise
      } else {
        pass_test &= d.content[f_test[i][0]].indexOf(f_test[i][1]) > -1; // eslint-disable-line no-bitwise
      }
      i += 1;
    }
    return pass_test;
  };

  if (f_test.length === 0) test = (d) => false;

  all_papers.forEach(function (paper) {
    paper.is_selected = test(paper);
  });
  updateVis();
};

const start = (track) => {
  const loadfiles = [
    d3.json("papers.json"),
    d3.json("serve_papers_projection.json"),
  ];
  if (track !== "All tracks") {
    loadfiles.push(d3.json(`track_${track}.json`));
  } else {
    trackhighlight = [];
  }
  Promise.all(loadfiles)
    .then(([papers, proj, trackPapers]) => {
      const projMap = new Map();
      proj.forEach((p) => projMap.set(p.id, p.pos));

      papers.forEach((p) => {
        p.pos = projMap.get(p.id);
      });

      // filter papers without a projection
      all_papers = papers.filter((p) => p.pos !== undefined);

      calcAllKeys(all_papers, allKeys);
      setTypeAhead("keywords", allKeys, filters, render);

      xS.domain(d3.extent(proj.map((p) => p.pos[0])));
      yS.domain(d3.extent(proj.map((p) => p.pos[1])));

      if (trackPapers) trackhighlight = trackPapers.map((d) => d.id);

      updateVis();
    })
    .catch((e) => console.error(e));
};

$(window).on("resize", _.debounce(updateVis, 150));

/**
 *  EVENTS
 * */

const updateFilterSelectionBtn = (value) => {
  d3.selectAll(".filter_option label").classed("active", function () {
    const v = d3.select(this).select("input").property("value");
    return v === value;
  });
};

d3.selectAll(".filter_option input").on("click", function () {
  const me = d3.select(this);

  const filter_mode = me.property("value");
  updateFilterSelectionBtn(filter_mode);

  setTypeAhead(filter_mode, allKeys, filters, render);
  render();
});
