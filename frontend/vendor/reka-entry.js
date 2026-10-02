/**
 * Entry point for the bundled `reka-ui` vendor chunk.
 *
 * NiceGUI serves the output of this file as a single ES module and puts it on
 * the page's import map under the bare specifier `reka-ui`, so our `.vue`
 * components can simply write:
 *
 *     import { CheckboxRoot } from 'reka-ui';
 *
 * Only the primitives that nicegui-shadcn actually wraps are re-exported, so
 * esbuild can tree-shake the rest of reka-ui away.
 *
 * `vue` is kept external: NiceGUI already puts its own Vue build on the import
 * map, and two copies of Vue would break provide/inject and Teleport.
 */
export {
  // -- disclosure ---------------------------------------------------------
  AccordionRoot,
  AccordionItem,
  AccordionHeader,
  AccordionTrigger,
  AccordionContent,
  CollapsibleRoot,
  CollapsibleTrigger,
  CollapsibleContent,
  // -- form controls ------------------------------------------------------
  CheckboxRoot,
  CheckboxIndicator,
  SwitchRoot,
  SwitchThumb,
  RadioGroupRoot,
  RadioGroupItem,
  RadioGroupIndicator,
  SliderRoot,
  SliderTrack,
  SliderRange,
  SliderThumb,
  Label,
  // -- select -------------------------------------------------------------
  SelectRoot,
  SelectTrigger,
  SelectValue,
  SelectIcon,
  SelectPortal,
  SelectContent,
  SelectViewport,
  SelectItem,
  SelectItemText,
  SelectItemIndicator,
  SelectGroup,
  SelectLabel,
  SelectSeparator,
  SelectArrow,
  SelectScrollUpButton,
  SelectScrollDownButton,
  // -- tabs ---------------------------------------------------------------
  TabsRoot,
  TabsList,
  TabsTrigger,
  TabsContent,
  // -- overlays -----------------------------------------------------------
  DialogRoot,
  DialogTrigger,
  DialogPortal,
  DialogOverlay,
  DialogContent,
  DialogTitle,
  DialogDescription,
  DialogClose,
  AlertDialogRoot,
  AlertDialogTrigger,
  AlertDialogPortal,
  AlertDialogOverlay,
  AlertDialogContent,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogAction,
  AlertDialogCancel,
  PopoverRoot,
  PopoverTrigger,
  PopoverPortal,
  PopoverContent,
  PopoverAnchor,
  TooltipProvider,
  TooltipRoot,
  TooltipTrigger,
  TooltipPortal,
  TooltipContent,
  TooltipArrow,
  HoverCardRoot,
  HoverCardTrigger,
  HoverCardPortal,
  HoverCardContent,
  DrawerRoot,
  DrawerTrigger,
  DrawerPortal,
  DrawerOverlay,
  DrawerContent,
  DrawerClose,
  DrawerTitle,
  DrawerDescription,
  DrawerHandle,
  // -- menus --------------------------------------------------------------
  DropdownMenuRoot,
  DropdownMenuTrigger,
  DropdownMenuPortal,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuCheckboxItem,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuGroup,
  DropdownMenuSub,
  DropdownMenuSubTrigger,
  DropdownMenuSubContent,
  ContextMenuRoot,
  ContextMenuTrigger,
  ContextMenuPortal,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuLabel,
  ContextMenuSeparator,
  MenubarRoot,
  MenubarMenu,
  MenubarTrigger,
  MenubarPortal,
  MenubarContent,
  MenubarItem,
  MenubarSeparator,
  MenubarLabel,
  NavigationMenuRoot,
  NavigationMenuList,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuTrigger,
  NavigationMenuContent,
  NavigationMenuViewport,
  NavigationMenuIndicator,
  // -- calendar -----------------------------------------------------------
  CalendarRoot,
  CalendarHeader,
  CalendarHeading,
  CalendarPrev,
  CalendarNext,
  CalendarGrid,
  CalendarGridHead,
  CalendarGridRow,
  CalendarGridBody,
  CalendarHeadCell,
  CalendarCell,
  CalendarCellTrigger,
  // -- misc primitives ----------------------------------------------------
  Toggle,
  ToggleGroupRoot,
  ToggleGroupItem,
  AvatarRoot,
  AvatarImage,
  AvatarFallback,
  ProgressRoot,
  ProgressIndicator,
  Separator,
  AspectRatio,
  ScrollAreaRoot,
  ScrollAreaViewport,
  ScrollAreaScrollbar,
  ScrollAreaThumb,
  ScrollAreaCorner,
  PinInputRoot,
  PinInputInput,
  // -- toasts -------------------------------------------------------------
  ToastProvider,
  ToastRoot,
  ToastTitle,
  ToastDescription,
  ToastAction,
  ToastClose,
  ToastViewport,
} from 'reka-ui';

/**
 * `@internationalized/date` rides along in this same chunk on purpose.
 *
 * reka-ui's calendar components import it with a bare specifier
 * (`import { isSameDay } from "@internationalized/date"`), which esbuild leaves
 * alone because the package is external to reka-ui's own build. Bundling it
 * here guarantees the page ends up with exactly one copy, so a `CalendarDate`
 * built by our Python-facing code still satisfies reka's internal `instanceof`
 * checks. reka-ui itself does not re-export any of these.
 *
 * Our `.vue` files cannot import the package directly: NiceGUI's VBuild ships a
 * component's `<script>` block as a raw ES module, so the only importable
 * specifiers are the ones on the page's import map (`vue` and `reka-ui`).
 */
export { CalendarDate, parseDate, today, getLocalTimeZone } from '@internationalized/date';
