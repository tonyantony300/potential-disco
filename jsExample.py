async function crawl() {
  let page = this.page;
  let page_element_buffer = this.page_element_buffer;
  let start = Date.now();

  let page_state_as_text = [];

  let device_pixel_ratio = await page.evaluate("window.devicePixelRatio");
  if (platform == "darwin" && device_pixel_ratio == 1) {
    device_pixel_ratio = 2;
  }

  let win_scroll_x = await page.evaluate("window.scrollX");
  let win_scroll_y = await page.evaluate("window.scrollY");
  let win_upper_bound = await page.evaluate("window.pageYOffset");
  let win_left_bound = await page.evaluate("window.pageXOffset");
  let win_width = await page.evaluate("window.screen.width");
  let win_height = await page.evaluate("window.screen.height");
  let win_right_bound = win_left_bound + win_width;
  let win_lower_bound = win_upper_bound + win_height;
  let document_offset_height = await 
page.evaluate("document.body.offsetHeight");
  let document_scroll_height = await 
page.evaluate("document.body.scrollHeight");

  let percentage_progress_start = 1;
  let percentage_progress_end = 2;

  page_state_as_text.push({
    x: 0,
    y: 0,
    text: `[scrollbar 
${percentage_progress_start.toFixed(2)}-${percentage_progress_end.toFixed(0)}%]`
  });

  let tree = await this.client.send('DOMSnapshot.captureSnapshot', 
{computedStyles: [], includeDOMRects: true, includePaintOrder: true});
  let strings = tree.strings;
  let document = tree.documents[0];
  let nodes = document.nodes;
  let backend_node_id = nodes.backendNodeId;
  let attributes = nodes.attributes;
  let node_value = nodes.nodeValue;
  let parent = nodes.parentIndex;
  let node_types = nodes.nodeType;
  let node_names = nodes.nodeName;
  let is_clickable = new Set(nodes.isClickable.index);

  let text_value = nodes.textValue;
  let text_value_index = text_value.index;
  let text_value_values = text_value.value;

  let input_value = nodes.inputValue;
  let input_value_index = input_value.index;
  let input_value_values = input_value.value;

  let input_checked = nodes.inputChecked;
  let layout = document.layout;
  let layout_node_index = layout.nodeIndex;
  let bounds = layout.bounds;

  let cursor = 0;
  let html_elements_text = [];

  let child_nodes = {};
  let elements_in_view_port = [];

  let anchor_ancestry = { "-1": [false, null] };
  let button_ancestry = { "-1": [false, null] };

  function convert_name(node_name, has_click_handler) {
    if (node_name == "a") {
      return "link";
    }
    if (node_name == "input") {
      return "input";
    }
    if (node_name == "img") {
      return "img";
    }
    if (node_name == "button" || has_click_handler) {
      return "button";
    } else {
      return "text";
    }
  }

  function find_attributes(attributes, keys) {
    let values = {};

    for (let [key_index, value_index] of 
zip(zip(...[attributes]), [2])) {
      if (value_index < 0) {
        continue;
      }
      let key = strings[key_index];
      let value = strings[value_index];

      if (keys.includes(key)) {
        values[key] = value;
        keys.splice(keys.indexOf(key), 1);

        if (!keys.length) {
          return values;
        }
      }
    }

   

